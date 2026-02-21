
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** AIDog
- **Date:** 2026-02-20
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 Install & Setup happy path: uv sync and Playwright Chromium install succeed
- **Test Code:** [TC001_Install__Setup_happy_path_uv_sync_and_Playwright_Chromium_install_succeed.py](./TC001_Install__Setup_happy_path_uv_sync_and_Playwright_Chromium_install_succeed.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Page title does not contain the text 'UI Dataset Builder'.
- Text 'Run uv sync' not found on the root page.
- Text 'playwright install chromium' not found on the root page.
- Text 'Chromium' not found on the root page.
- Text 'environment ready' not found on the root page.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/08c9825a-08c3-4d43-9c31-e08fe19a793f
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 Install & Setup documentation is discoverable from the Landing page CTA
- **Test Code:** [TC002_Install__Setup_documentation_is_discoverable_from_the_Landing_page_CTA.py](./TC002_Install__Setup_documentation_is_discoverable_from_the_Landing_page_CTA.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Get Started CTA did not navigate to a page whose URL contains 'setup' after multiple click attempts.
- Landing page remained at 'http://localhost:3000/' with landing content visible after clicking the CTA.
- No visible page content containing the word 'Install' was found after clicking the CTA.
- No visible page content containing the text 'uv sync' was found after clicking the CTA.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/883851fd-6308-45c7-9bbb-e776e294140c
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 Install & Setup: error path messaging for uv sync dependency resolution failure is visible
- **Test Code:** [TC003_Install__Setup_error_path_messaging_for_uv_sync_dependency_resolution_failure_is_visible.py](./TC003_Install__Setup_error_path_messaging_for_uv_sync_dependency_resolution_failure_is_visible.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Required guidance text 'Dependency resolution fails' not found on site root install/setup section.
- Required guidance text 'missing system packages' not found on site root install/setup section.
- Required guidance text 'suggested fixes' not found on site root install/setup section.
- Required guidance text 'uv sync' not found on site root install/setup section.
- Incidents flow could not be inspected because authentication/incident access was not established (login attempts exhausted).
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/1267c4a6-d327-4f2d-a5f2-586f1da38fc9
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 Install & Setup: Playwright Chromium install step is explicitly called out
- **Test Code:** [TC004_Install__Setup_Playwright_Chromium_install_step_is_explicitly_called_out.py](./TC004_Install__Setup_Playwright_Chromium_install_step_is_explicitly_called_out.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/674fd232-cdea-48a1-bde9-d5dfb00bac9d
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 Install & Setup: prerequisites mention for system packages is present
- **Test Code:** [TC005_Install__Setup_prerequisites_mention_for_system_packages_is_present.py](./TC005_Install__Setup_prerequisites_mention_for_system_packages_is_present.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Prerequisites heading not found on the website's root page.
- Install/setup instructions section not present on the root page after scrolling and searching.
- Text 'system packages' not present on the site.
- Text 'Linux' not present on the site.
- Text 'macOS' not present on the site.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/a4d45b22-ed21-4893-8b37-356e8fa4b4c2
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 Install & Setup: instructions include a clear sequence from clone to ready state
- **Test Code:** [TC006_Install__Setup_instructions_include_a_clear_sequence_from_clone_to_ready_state.py](./TC006_Install__Setup_instructions_include_a_clear_sequence_from_clone_to_ready_state.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Install/setup instructions section not found on the homepage at '/'.
- Text 'Clone' not found on the page.
- Text 'uv sync' not found on the page.
- Text 'playwright install chromium' not found on the page.
- Text 'ready' not found on the page.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/ff546ad3-dbde-438a-94c6-b847fa62c92e
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 Build workflow guidance is discoverable from the Landing page
- **Test Code:** [TC007_Build_workflow_guidance_is_discoverable_from_the_Landing_page.py](./TC007_Build_workflow_guidance_is_discoverable_from_the_Landing_page.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/677fb1a9-41da-458e-9828-ca07bd8a4786
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 Build run prerequisites are understandable from UI copy (no CLI execution)
- **Test Code:** [TC008_Build_run_prerequisites_are_understandable_from_UI_copy_no_CLI_execution.py](./TC008_Build_run_prerequisites_are_understandable_from_UI_copy_no_CLI_execution.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Text 'URLs' not found on the landing page under the main workflow or elsewhere
- Text 'screenshots' not found on the landing page under the main workflow or elsewhere
- Text 'annotations' not found on the landing page under the main workflow or elsewhere
- Text 'COCO' not found on the landing page under the main workflow or elsewhere
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/ccc524ac-1b4f-4582-9d6c-026e05c8f419
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 Configure crawl options with valid flags and verify run summary reflects settings
- **Test Code:** [TC009_Configure_crawl_options_with_valid_flags_and_verify_run_summary_reflects_settings.py](./TC009_Configure_crawl_options_with_valid_flags_and_verify_run_summary_reflects_settings.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Text 'UI Dataset Builder' not found on the homepage; landing page shows AIDog hero content instead.
- Required 'UI Dataset Builder' feature/page is missing, so viewport/concurrency/scroll/wait strategy settings cannot be verified in a build run output/summary.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/ed52934b-4660-408f-a5f3-7828e89ed990
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 Invalid viewport flag shows validation error and prevents run
- **Test Code:** [TC010_Invalid_viewport_flag_shows_validation_error_and_prevents_run.py](./TC010_Invalid_viewport_flag_shows_validation_error_and_prevents_run.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login link clicked but login form did not open; no email, password, or Sign In interactive elements found on the current page.
- Required login inputs (email, password) or Sign In button not present to perform authentication.
- Cannot reach authenticated area ('/home') to verify the presence of the validation message 'invalid viewport format'.
- No clickable element index for the 'Login' control is available on the homepage, preventing continuation of the login flow.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/c0249e01-0396-43f5-a996-e8d76a79e244
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC011 Crawl run shows evidence of extra scroll screenshots setting
- **Test Code:** [TC011_Crawl_run_shows_evidence_of_extra_scroll_screenshots_setting.py](./TC011_Crawl_run_shows_evidence_of_extra_scroll_screenshots_setting.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login did not complete - application remained on '/login' after multiple sign-in attempts and the UI showed a persistent 'Signing in...' state.
- Authenticated '/home' page was not reached after submitting valid test credentials; URL did not change to contain '/home'.
- Incidents page could not be accessed because authentication failed, so verification of scroll-capture evidence/screenshots cannot be performed.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/1513354a-b9d2-4f9b-ab50-b5fd9885db15
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC012 Configured concurrency is displayed in the run configuration details
- **Test Code:** [TC012_Configured_concurrency_is_displayed_in_the_run_configuration_details.py](./TC012_Configured_concurrency_is_displayed_in_the_run_configuration_details.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login did not complete after two sign-in attempts: the application remained on the login page showing the sign-in form.
- Current URL is '/login' and no redirect to '/home' occurred after the sign-in attempts.
- Credentials were entered and the Sign In button was clicked twice, but no navigation to dashboard/incidents was observed.
- Unable to verify the 'Concurrency' value because post-login pages (home/incidents/run configuration) could not be reached.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/901cdb84-3141-452d-b04c-c52eb42df069
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC013 Configured viewport is displayed and reflected in capture metadata
- **Test Code:** [TC013_Configured_viewport_is_displayed_and_reflected_in_capture_metadata.py](./TC013_Configured_viewport_is_displayed_and_reflected_in_capture_metadata.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login failed - application remained on the login page after two sign-in attempts and did not redirect to /home.
- Dashboard '/home' not reachable - URL does not contain '/home' and authenticated pages were not accessible.
- Viewport setting '1280x720' could not be verified because authentication was not achieved and the capture configuration/metadata pages were not accessible.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/5149ac99-03e4-4c1d-9000-5f2a88b9d43d
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC014 Wait strategy networkidle is shown in crawl/run settings
- **Test Code:** [TC014_Wait_strategy_networkidle_is_shown_in_crawlrun_settings.py](./TC014_Wait_strategy_networkidle_is_shown_in_crawlrun_settings.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Current URL remains on the login page (contains '/login') after sign-in attempts.
- The application shows 'Signing in...' with Email and Password inputs still visible, indicating authentication did not complete.
- The application did not navigate to '/home' after submission, so the run configuration or incident pages were not reached.
- The text 'networkidle' (the page-load wait strategy indicator) was not visible on any reachable page during this session.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/9afca319-95a7-4385-b3d3-0d1c73ab4939
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC015 Export both formats with selected classes shows COCO and YOLO outputs in the UI
- **Test Code:** [TC015_Export_both_formats_with_selected_classes_shows_COCO_and_YOLO_outputs_in_the_UI.py](./TC015_Export_both_formats_with_selected_classes_shows_COCO_and_YOLO_outputs_in_the_UI.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Sign In button not actionable; login form remains and 'Signing in...' state persists after submitting credentials
- No redirect to post-login page (e.g., /home or /incidents) observed after multiple login attempts
- Unable to access incident investigation flow; dataset build steps cannot be reached because authentication did not complete
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/85e5e521-8c58-48c8-a0e8-5db03d6f1668
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC016 Export both formats lists COCO JSON output path
- **Test Code:** [TC016_Export_both_formats_lists_COCO_JSON_output_path.py](./TC016_Export_both_formats_lists_COCO_JSON_output_path.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login did not complete after two attempts; the page remains on /login instead of redirecting to /home.
- 'Signing in...' indicator appeared during attempts but no successful authentication or redirect occurred.
- Authenticated pages (e.g., Build Dataset / New Build) could not be reached because the user remains unauthenticated.
- Email and Password input fields and the Sign In button are still visible, indicating the app is still on the login screen.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/096bb980-4294-4b2e-8f87-fe7f200897a2
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC017 Export both formats lists YOLO output folder or files
- **Test Code:** [TC017_Export_both_formats_lists_YOLO_output_folder_or_files.py](./TC017_Export_both_formats_lists_YOLO_output_folder_or_files.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login failed: the application remained on the login page after multiple submission attempts.
- Sign In button not present as a clickable interactive element on the page, preventing reliable form submission.
- Could not access authenticated pages (e.g., /home, incidents) required to reach Build Dataset / New Build views.
- Build Dataset / New Build CTA and build results could not be reached or verified because authentication did not complete.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/9656e75b-cf25-4b88-af04-e36182ad03a9
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC018 Selecting a class taxonomy subset shows the chosen classes in the export configuration summary
- **Test Code:** [TC018_Selecting_a_class_taxonomy_subset_shows_the_chosen_classes_in_the_export_configuration_summary.py](./TC018_Selecting_a_class_taxonomy_subset_shows_the_chosen_classes_in_the_export_configuration_summary.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login did not complete - application remained on the login page (http://localhost:3000/login) after submitting credentials.
- Signing-in state observed but no redirect to the post-login page (/home) occurred.
- Build Dataset / New Build call-to-action not accessible because the user is not authenticated.
- Classes input or UI for entering included classes could not be located; unable to verify 'button,link,input,checkbox,image_icon' is visible.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/cee55864-4034-4aab-a449-18c8e351d509
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC019 Export both formats with class subset completes successfully
- **Test Code:** [TC019_Export_both_formats_with_class_subset_completes_successfully.py](./TC019_Export_both_formats_with_class_subset_completes_successfully.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Authentication did not complete: the login page (email input index 193, password input index 194) remained visible after two sign-in attempts.
- /home or /incidents pages were not reached due to failed authentication, preventing access to the Build Dataset flow.
- Build/run steps could not be executed because the user is not authenticated and further identical login attempts are disallowed.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/0e305461-0016-493f-a294-9230e900751e
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC020 Unsupported export format shows a clear validation error and does not start export
- **Test Code:** [TC020_Unsupported_export_format_shows_a_clear_validation_error_and_does_not_start_export.py](./TC020_Unsupported_export_format_shows_a_clear_validation_error_and_does_not_start_export.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login did not complete: application remained on the login page after two sign-in submissions.
- Authentication did not reach the authenticated '/home' area; URL did not change to contain '/home'.
- Build Dataset / New Build CTA could not be tested because user authentication was not established.
- Sign In control became non-interactive or remained in a 'Signing in...' state, preventing progression to the next steps.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/47082c02-850d-4713-a012-adddc90bb5e4
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC021 Unsupported export format attempt exits the run flow (no outputs shown)
- **Test Code:** [TC021_Unsupported_export_format_attempt_exits_the_run_flow_no_outputs_shown.py](./TC021_Unsupported_export_format_attempt_exits_the_run_flow_no_outputs_shown.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/2086b922-8217-4a3a-abc2-4fa74a119a29
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC022 Classes field rejects invalid/empty taxonomy input
- **Test Code:** [TC022_Classes_field_rejects_invalidempty_taxonomy_input.py](./TC022_Classes_field_rejects_invalidempty_taxonomy_input.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login failed - application remains on the login page and is stuck in a 'Signing in...' state after multiple attempts.
- Sign In button not actionable or session not established after 4 authentication attempts using the provided test credentials.
- Post-login URL (/home) and post-login UI (Build Dataset / New Build) are not present, preventing navigation to the feature under test.
- Classes input validation could not be tested because the application could not be reached beyond the login screen.
- Interactive elements required for the next steps (Build Dataset/New Build, Classes field) are not available on the current page.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/837abf4e-909a-4e96-abbc-2e58872e68ee
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC023 Signup page loads and role selection is visible
- **Test Code:** [TC023_Signup_page_loads_and_role_selection_is_visible.py](./TC023_Signup_page_loads_and_role_selection_is_visible.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/8d657da4-0c9f-4155-81ad-592eb4a011d7
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC024 Landing page surfaces legal/robots guidance in product messaging
- **Test Code:** [TC024_Landing_page_surfaces_legalrobots_guidance_in_product_messaging.py](./TC024_Landing_page_surfaces_legalrobots_guidance_in_product_messaging.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/478de95b-1035-4546-ae0a-52e0097fe8f0
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC025 Warning about default not respecting robots.txt is visible to users
- **Test Code:** [TC025_Warning_about_default_not_respecting_robots.txt_is_visible_to_users.py](./TC025_Warning_about_default_not_respecting_robots.txt_is_visible_to_users.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Required warning text 'respect-robots' not found on homepage at http://localhost:3000/.
- Required warning text 'false by default' not found on homepage at http://localhost:3000/.
- Required warning text 'ensure you have permission' not found on homepage at http://localhost:3000/.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/aefc3e99-1b7e-49c3-8cde-7403d9eaa16d
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC026 Robots respect option is documented as an explicit opt-in
- **Test Code:** [TC026_Robots_respect_option_is_documented_as_an_explicit_opt_in.py](./TC026_Robots_respect_option_is_documented_as_an_explicit_opt_in.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- '--respect-robots' UI copy not found on the root or login pages after multiple searches, indicating the feature/copy is missing or not publicly visible.
- 'option' keyword not found on the root or login pages in the context of robots.txt, so there is no visible indication that respecting robots.txt is presented as an explicit option/flag.
- Incidents flow could not be inspected for this UI copy because navigation to /incidents redirected to /login, preventing verification inside the authenticated incident investigation screens.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/08c37828-99de-40f9-840f-bf937bc40675
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC027 Legal guidance is accessible without authentication
- **Test Code:** [TC027_Legal_guidance_is_accessible_without_authentication.py](./TC027_Legal_guidance_is_accessible_without_authentication.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- 'robots.txt' not found on the public site root page (legal/robots guidance not visible).
- 'ensure' text not found on the public site root page (expected legal/guidance text missing).
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/d2108176-4370-48ea-a46d-5fd8ea6e7004
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC028 Login page does not block access to legal/robots guidance discovery
- **Test Code:** [TC028_Login_page_does_not_block_access_to_legalrobots_guidance_discovery.py](./TC028_Login_page_does_not_block_access_to_legalrobots_guidance_discovery.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/51fe54af-b22c-44ce-af7f-ad8913910089
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC029 Signup page is accessible and does not imply robots respect is automatic
- **Test Code:** [TC029_Signup_page_is_accessible_and_does_not_imply_robots_respect_is_automatic.py](./TC029_Signup_page_is_accessible_and_does_not_imply_robots_respect_is_automatic.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/4125535f-67e5-447e-8714-f88bfc21e5d1
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC030 Legal/robots guidance remains visible after scrolling through landing content
- **Test Code:** [TC030_Legalrobots_guidance_remains_visible_after_scrolling_through_landing_content.py](./TC030_Legalrobots_guidance_remains_visible_after_scrolling_through_landing_content.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/7ef8e694-afc3-4ac3-98df-b7d61c828436
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC031 Login and reach authenticated Home dashboard
- **Test Code:** [TC031_Login_and_reach_authenticated_Home_dashboard.py](./TC031_Login_and_reach_authenticated_Home_dashboard.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/48ce28b0-1a5f-4e8c-8278-3f724d877306
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC032 Navigate to Incidents list from Home
- **Test Code:** [TC032_Navigate_to_Incidents_list_from_Home.py](./TC032_Navigate_to_Incidents_list_from_Home.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Login failed - page still shows the login form and URL path is '/login' after two sign-in attempts.
- Sign-in action did not complete - the sign-in button remains in state 'Signing in...' indicating the authentication process is stuck or blocked.
- Incidents navigation could not be accessed - the Incidents list was not reached because the user remained unauthenticated.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/8005d009-b1df-488c-8072-17e19b09317a
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC033 Incidents list shows severity badges and timestamps
- **Test Code:** [TC033_Incidents_list_shows_severity_badges_and_timestamps.py](./TC033_Incidents_list_shows_severity_badges_and_timestamps.py)
- **Test Error:** TEST FAILURE

ASSERTIONS:
- Sign-in did not complete: after two 'Sign In' attempts the login form remains visible and the application did not redirect to the Incidents list or dashboard.
- Access to the Incidents page could not be verified because authentication failed and main navigation to Incidents was not reachable.
- No explicit authentication success or informative error message was presented after submitting the login form.
- Test credentials were entered into the email and password fields (email='example@gmail.com') but were not accepted.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/1a88d06d-24cd-4546-b5f6-15d880503d1a
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC034 Invalid password shows an error message
- **Test Code:** [TC034_Invalid_password_shows_an_error_message.py](./TC034_Invalid_password_shows_an_error_message.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/0ffacb91-0a62-4bcd-926e-3e26a253027f
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC035 Signup page renders required fields including role selection
- **Test Code:** [TC035_Signup_page_renders_required_fields_including_role_selection.py](./TC035_Signup_page_renders_required_fields_including_role_selection.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/6764144e-b8d9-493e-aefa-508a507138cf/2e4afe02-06bc-4fae-bf23-d8224d3fad19
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **31.43** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---