#!/usr/bin/env python3
"""One-time AWS Bedrock AgentCore setup script.

Run this ONCE to provision:
  1. IAM execution role for the Gateway
  2. AgentCore Memory resource  → prints AGENTCORE_MEMORY_ID
  3. AgentCore Gateway          → prints AGENTCORE_GATEWAY_ID
  4. Gateway Tool Target        → registers the AIDog tool spec

After running, copy the printed IDs into backend/.env.

Usage:
    cd backend
    source venv/bin/activate
    python agentcore_deploy.py [--region us-east-2]
"""
import argparse
import json
import sys
import time

try:
    import boto3
except ImportError:
    print("ERROR: boto3 not installed. Run: pip install boto3", file=sys.stderr)
    sys.exit(1)

from app.agentcore.gateway import TOOL_OPENAPI_SPEC

MEMORY_NAME = "aidog_investigation_memory"
GATEWAY_NAME = "aidog-observability-gateway"
ROLE_NAME = "AIDogAgentCoreGatewayRole"


# ── IAM Role ──────────────────────────────────────────────────────────────────

def ensure_gateway_role(account_id: str, region: str) -> str:
    """Create (or return existing) IAM execution role for the AgentCore Gateway."""
    print("Ensuring IAM execution role for Gateway...")
    iam = boto3.client("iam")

    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }]
    })

    try:
        resp = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=trust_policy,
            Description="Execution role for AIDog AgentCore Gateway",
        )
        role_arn = resp["Role"]["Arn"]
        # Attach a basic execution policy
        iam.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName="AgentCoreGatewayExecution",
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:*",
                        "logs:CreateLogGroup",
                        "logs:CreateLogDelivery",
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                }]
            }),
        )
        print(f"  ✓ IAM role created: {role_arn}")
        # Brief pause for IAM propagation
        time.sleep(5)
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"
        print(f"  ✓ IAM role already exists: {role_arn}")

    return role_arn


# ── Memory ────────────────────────────────────────────────────────────────────

def create_memory_resource(client) -> str:
    """Create an AgentCore Memory resource and return its ID."""
    print("Creating AgentCore Memory resource...")

    def _find_existing() -> str:
        resp = client.list_memories()
        items = resp.get("memories") or resp.get("memorySummaries") or []
        for mem in items:
            mem_id = mem.get("id") or mem.get("memoryId") or ""
            if mem_id.startswith(MEMORY_NAME):
                print(f"  ✓ Memory already exists: {mem_id}")
                return mem_id
        # Nothing matched — return first item's id if only one exists
        if len(items) == 1:
            mem_id = items[0].get("id") or items[0].get("memoryId") or ""
            print(f"  ✓ Using existing memory: {mem_id}")
            return mem_id
        print(f"  ⚠ Could not locate memory. Raw list: {items}")
        return ""

    try:
        resp = client.create_memory(
            name=MEMORY_NAME,
            description="Per-session ephemeral working memory for AIDog incident investigations",
            eventExpiryDuration=30,
        )
        memory_id = resp.get("id") or resp.get("memoryId") or ""
        print(f"  ✓ Memory created: {memory_id}")
        return memory_id
    except Exception as exc:
        if "already exists" in str(exc).lower():
            return _find_existing()
        raise


# ── Gateway ───────────────────────────────────────────────────────────────────

def create_gateway(client, role_arn: str) -> str:
    """Create an AgentCore Gateway and return its ID."""
    print("Creating AgentCore Gateway...")

    # Check for existing gateway first to avoid unnecessary PassRole calls
    resp = client.list_gateways()
    items = resp.get("items") or resp.get("gateways") or resp.get("gatewaySummaries") or []
    for gw in items:
        gw_id = gw.get("gatewayId") or gw.get("id") or ""
        gw_name = gw.get("name") or ""
        if gw_name == GATEWAY_NAME or gw_id.startswith(GATEWAY_NAME):
            print(f"  ✓ Gateway already exists: {gw_id}")
            return gw_id

    try:
        resp = client.create_gateway(
            name=GATEWAY_NAME,
            description="Tool gateway for AIDog observability tools (Datadog, Toto, TestSprite)",
            roleArn=role_arn,
            protocolType="MCP",
            authorizerType="NONE",
        )
        gateway_id = resp.get("gatewayId") or resp.get("id") or ""
        print(f"  ✓ Gateway created: {gateway_id}")
        return gateway_id
    except Exception as exc:
        if "already exists" in str(exc).lower() or "conflict" in str(exc).lower():
            if items:
                gw_id = items[0].get("gatewayId") or items[0].get("id") or ""
                print(f"  ✓ Using existing gateway: {gw_id}")
                return gw_id
        raise


# ── Gateway Target ────────────────────────────────────────────────────────────

def ensure_api_key_credential_provider(client) -> str:
    """Create (or return existing) API key credential provider and return its ARN."""
    print("Ensuring API key credential provider...")
    provider_name = "aidog-api-key-provider"

    # Check if already exists
    try:
        resp = client.list_api_key_credential_providers()
        items = resp.get("items") or resp.get("apiKeyCredentialProviders") or []
        for item in items:
            if item.get("name") == provider_name:
                arn = item.get("credentialProviderArn") or item.get("arn") or ""
                print(f"  ✓ Credential provider already exists: {arn}")
                return arn
    except Exception:
        pass

    import secrets
    resp = client.create_api_key_credential_provider(
        name=provider_name,
        apiKey=secrets.token_hex(32),
    )
    arn = resp.get("credentialProviderArn") or resp.get("arn") or ""
    print(f"  ✓ Credential provider created: {arn}")
    return arn


def register_gateway_tools(client, gateway_id: str, credential_provider_arn: str) -> None:
    """Register the AIDog tool OpenAPI spec as a Gateway Target."""
    print("Registering tool definitions in Gateway...")

    # Check if target already exists
    try:
        resp = client.list_gateway_targets(gatewayIdentifier=gateway_id)
        items = resp.get("items") or resp.get("gatewayTargets") or []
        for item in items:
            if item.get("name") == "aidog-observability-tools":
                print("  ✓ Tool target already registered (skipped).")
                return
    except Exception:
        pass

    try:
        client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="aidog-observability-tools",
            description="Datadog, Toto, and TestSprite tools for incident investigation",
            targetConfiguration={
                "mcp": {
                    "openApiSchema": {
                        "inlinePayload": json.dumps(TOOL_OPENAPI_SPEC),
                    }
                }
            },
            credentialProviderConfigurations=[
                {
                    "credentialProviderType": "API_KEY",
                    "credentialProvider": {
                        "apiKeyCredentialProvider": {
                            "providerArn": credential_provider_arn,
                            "credentialParameterName": "x-api-key",
                            "credentialLocation": "HEADER",
                        }
                    },
                }
            ],
        )
        print("  ✓ Tool target registered.")
    except Exception as exc:
        if "already exists" in str(exc).lower() or "conflict" in str(exc).lower():
            print("  ✓ Tool target already registered (skipped).")
        else:
            print(f"  ⚠ Tool target registration failed: {exc}")
            print("    You can register it manually via the AWS Console.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AIDog AgentCore one-time setup")
    parser.add_argument("--region", default="us-east-2", help="AWS region")
    parser.add_argument(
        "--role-arn",
        help="IAM role ARN for the Gateway execution role (skip auto-creation)",
    )
    args = parser.parse_args()

    region = args.region
    print(f"\n=== AIDog AgentCore Setup (region: {region}) ===\n")

    sts = boto3.client("sts", region_name=region)
    account_id = sts.get_caller_identity()["Account"]

    if args.role_arn:
        role_arn = args.role_arn
        print(f"Using provided role ARN: {role_arn}")
    else:
        try:
            role_arn = ensure_gateway_role(account_id, region)
        except Exception as exc:
            if "AccessDenied" in str(exc) or "not authorized" in str(exc).lower():
                print(f"\n⚠ Cannot create IAM role automatically ({exc})")
                print("\nCreate the role manually in the AWS Console:")
                print("  1. Go to IAM → Roles → Create role")
                print("  2. Trusted entity type: AWS service → bedrock-agentcore.amazonaws.com")
                print(f"  3. Role name: {ROLE_NAME}")
                print("  4. Add permission: AmazonBedrockFullAccess (or a scoped policy)")
                print(f"  5. Copy the Role ARN and re-run:")
                print(f"     AWS_PROFILE=yash python3 agentcore_deploy.py --region {region} --role-arn <paste ARN here>")
                sys.exit(1)
            raise

    control_client = boto3.client("bedrock-agentcore-control", region_name=region)

    memory_id = create_memory_resource(control_client)
    gateway_id = create_gateway(control_client, role_arn)
    if gateway_id:
        credential_provider_arn = ensure_api_key_credential_provider(control_client)
        register_gateway_tools(control_client, gateway_id, credential_provider_arn)

    print("\n=== Add these to backend/.env ===\n")
    print(f"AWS_REGION={region}")
    print(f"AGENTCORE_MEMORY_ID={memory_id}")
    print(f"AGENTCORE_GATEWAY_ID={gateway_id}")
    print("\n✓ Done. Restart the backend after updating .env.\n")


if __name__ == "__main__":
    main()
