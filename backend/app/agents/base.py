"""Base agent class with Minimax integration."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, Dict, Any, List, get_origin
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefinedType
import json

from app.core.minimax_client import get_minimax_client, MinimaxClient
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC, Generic[T]):
    """Base class for all agents with Minimax integration."""

    def __init__(
        self,
        client: Optional[MinimaxClient] = None,
        temperature: Optional[float] = None,
    ):
        self.client = client or get_minimax_client()
        self.temperature = temperature or self.client.temperature
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        pass

    @abstractmethod
    def get_output_schema(self) -> Type[T]:
        """Get Pydantic schema for output validation."""
        pass

    def format_messages(
        self, user_prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Format messages for Minimax API."""
        messages = []

        # Add context if provided
        if context:
            context_str = json.dumps(context, indent=2)
            messages.append({
                "role": "user",
                "content": f"Context:\n{context_str}\n\nTask:\n{user_prompt}",
            })
        else:
            messages.append({"role": "user", "content": user_prompt})

        return messages

    async def execute(
        self,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> T:
        """
        Execute agent with prompt and return validated output.

        Args:
            user_prompt: User prompt/instruction
            context: Optional context dictionary
            temperature: Override default temperature

        Returns:
            Validated Pydantic model instance
        """
        system_prompt = self.get_system_prompt()
        messages = self.format_messages(user_prompt, context)
        schema = self.get_output_schema()

        try:
            # Call Minimax API
            response = await self.client.chat_json(
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or 2000,
            )

            # Validate against schema
            try:
                result = schema(**response)
                self.logger.info(f"Agent {self.__class__.__name__} executed successfully")
                return result
            except ValidationError as e:
                self.logger.error(f"Schema validation failed: {e}")
                # Try to extract valid fields and create fallback
                return self._create_fallback(response, schema)

        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return self._create_fallback({}, schema)

    def _create_fallback(
        self, response: Dict[str, Any], schema: Type[T]
    ) -> T:
        """Create fallback response when validation fails."""
        # Try to create schema with minimal required fields
        try:
            # Get default values from schema
            defaults = {}
            for field_name, field_info in schema.model_fields.items():
                if (hasattr(field_info, "default")
                        and field_info.default is not None
                        and not isinstance(field_info.default, PydanticUndefinedType)):
                    defaults[field_name] = field_info.default
                elif field_info.is_required():
                    # Provide empty defaults — use get_origin() for generics like List[X]
                    ann = field_info.annotation
                    origin = get_origin(ann)
                    if ann is str or ann == str:
                        defaults[field_name] = ""
                    elif ann is list or origin is list:
                        defaults[field_name] = []
                    elif ann is dict or origin is dict:
                        defaults[field_name] = {}
                    elif ann is int or ann == int:
                        defaults[field_name] = 0

            # Merge with response
            merged = {**defaults, **response}
            return schema(**merged)
        except Exception as e:
            self.logger.error(f"Fallback creation failed: {e}")
            # Return minimal valid instance
            return schema.model_construct(**defaults)
