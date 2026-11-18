# Acceptance-test family index

Revision 2.0, 18 November 2026. Source `b3d900f`; saved current Linux result: 110 tests passed in 3.087 s.

TC IDs are requirement acceptance families, not executable-test counts. The list below is extracted from the current test method names; test execution evidence is [student-lifecycle-tests.txt](../development/student-lifecycle-tests.txt). Some tests support multiple families. Manual criteria still apply, especially TC019–TC025.

## TC001 — FR001

- `tests/test_application.py::test_TC001_anonymous_pages_and_apis`
- `tests/test_application.py::test_TC001_valid_invalid_and_inactive_login`
- `tests/test_application.py::test_TC001_invalid_or_multiple_roles_cannot_sign_in`

## TC002 — FR002

- `tests/test_application.py::test_TC002_logout_invalidates_previous_session`

## TC003 — FR003

- `tests/test_application.py::test_TC003_student_cannot_access_organizer_endpoints`
- `tests/test_application.py::test_TC003_other_students_registration_is_not_accessible`

## TC004 — FR004

- `tests/test_application.py::test_TC004_create_draft_and_hide_from_students`
- `tests/test_application.py::test_TC004_invalid_capacity_and_time_never_create`

## TC005 — FR005

- `tests/test_application.py::test_TC005_edit_draft_and_published_rules`
- `tests/test_application.py::test_TC005_started_and_cancelled_events_read_only`

## TC006 — FR006

- `tests/test_application.py::test_TC006_publish_once_and_reject_expired_draft`

## TC007 — FR007

- `tests/test_application.py::test_TC007_search_category_date_and_empty_filters`

## TC008 — FR008

- `tests/test_application.py::test_TC008_availability_and_no_participant_identity`

## TC009 — FR009

- `tests/test_application.py::test_TC009_capacity_allocation_and_no_GET_mutations`
- `tests/test_application.py::test_TC009_deadline_equality_rejected`

## TC010 — FR010

- `tests/test_application.py::test_TC010_retries_and_database_uniqueness`

## TC011 — FR011

- `tests/test_application.py::test_TC011_personal_history_and_queue_rank`

## TC012 — FR012

- `tests/test_application.py::test_TC012_repeated_cancel_and_rejoin_new_priority`
- `tests/test_application.py::test_TC012_cancel_at_deadline_does_not_change_state`

## TC013 — FR013

- `tests/test_application.py::test_TC013_FIFO_promotion_and_idempotent_cancellation`
- `tests/test_application.py::test_TC013_equal_timestamps_use_id_tiebreaker`
- `tests/test_application.py::test_TC013_promotion_failure_rolls_back_cancellation`
- `tests/test_application.py::test_TC013_cancel_response_does_not_reveal_promoted_student`

## TC014 — FR014

- `tests/test_application.py::test_TC014_event_cancellation_preserves_history_no_promotion`
- `tests/test_application.py::test_TC014_blank_reason_and_started_cancellation_rejected`

## TC015 — FR015

- `tests/test_application.py::test_TC015_roster_filter_identity_and_queue_order`

## TC016 — FR016

- `tests/test_application.py::test_TC016_attendance_boundary_audit_and_correction`

## TC017 — FR017

- `tests/test_application.py::test_TC017_summary_excludes_draft_cancelled_and_started`

## TC018 — FR018

- `tests/test_application.py::test_TC018_malformed_and_tampered_requests_rejected`
- `tests/test_application.py::test_TC018_lock_failure_returns_retryable_error`

## TC019 — NFR001

- `tests/test_application.py::test_TC019_local_30_events_300_registrations`

## TC020 — NFR002

- `tests/test_application.py::test_TC020_csrf_missing_and_valid_token`
- `tests/test_application.py::test_TC020_escaped_text_and_hash_storage`

## TC021 — NFR003

- `tests/test_transactions.py::test_TC021_competing_requests_for_last_seat`
- `tests/test_transactions.py::test_TC021_concurrent_duplicate_requests`
- `tests/test_transactions.py::test_TC021_registration_persists_after_connection_restart`
- `tests/test_transactions.py::test_TC021_event_cancellation_rolls_back_on_update_failure`

## TC022 — NFR004

- `tests/test_application.py::test_TC022_all_required_pages_render`

## TC023 — NFR005

Manual/setup/evaluator acceptance; see the requirement’s evidence and acceptance criteria. Critical-rule automated methods support TC023, but no method is named TC023 or TC024.

## TC024 — NFR006

Manual/setup/evaluator acceptance; see the requirement’s evidence and acceptance criteria. Critical-rule automated methods support TC023, but no method is named TC023 or TC024.

## TC025 — NFR007

- `tests/test_backup.py::test_TC025_backup_closes_connections_before_return`
- `tests/test_backup.py::test_TC025_failed_backup_closes_connections_before_cleanup`
- `tests/test_backup.py::test_TC025_destination_open_failure_closes_source`
- `tests/test_backup.py::test_TC025_integrity_failure_closes_connections_before_cleanup`
- `tests/test_transactions.py::test_TC025_backup_restore_exact_rows_and_no_overwrite`

## TC026 — FR019

- `tests/test_user_management.py::test_TC026_anonymous_and_students_cannot_access_management`
- `tests/test_user_management.py::test_TC026_navigation_is_organizer_only`
- `tests/test_user_management.py::test_TC026_search_name_username_id_and_email`
- `tests/test_user_management.py::test_TC026_search_limits_and_pagination`
- `tests/test_user_management.py::test_TC026_organizers_and_privileged_or_invalid_students_are_protected`
- `tests/test_user_management.py::test_TC026_sensitive_pages_are_not_cached_and_unknown_ids_are_404`

## TC027 — FR020

- `tests/test_user_management.py::test_TC027_saves_details_and_preserves_registration_rows_and_password`
- `tests/test_user_management.py::test_TC027_duplicate_id_is_rejected_without_partial_user_changes`
- `tests/test_user_management.py::test_TC027_validation_rejects_blank_overlong_and_invalid_values`
- `tests/test_user_management.py::test_TC027_optional_fields_and_trimmed_values`
- `tests/test_user_management.py::test_TC027_tampered_privilege_and_identity_fields_are_rejected`
- `tests/test_user_management.py::test_TC027_post_requires_csrf_and_other_write_methods_are_rejected`
- `tests/test_user_management.py::test_TC027_get_requests_never_change_records`
- `tests/test_user_management.py::test_TC027_integrity_failure_rolls_back_name_and_email`
- `tests/test_user_management.py::test_TC027_database_lock_is_retryable_and_rolls_back`
- `tests/test_user_management.py::test_TC027_names_and_search_text_are_html_escaped`

## TC028 — FR021

- `tests/test_user_management.py::test_TC028_password_reset_invalidates_student_session_only`
- `tests/test_user_management.py::test_TC028_weak_or_mismatched_passwords_do_not_change_account`
- `tests/test_user_management.py::test_TC028_reset_rejects_privilege_fields_and_does_not_reactivate`

## TC029 — FR022

- `tests/test_student_accounts.py::test_TC029_create_stores_hashed_password_and_fixed_student_role`
- `tests/test_student_accounts.py::test_TC029_created_student_can_register_and_view_own_history`
- `tests/test_student_accounts.py::test_TC029_only_active_single_role_organizers_can_create`
- `tests/test_student_accounts.py::test_TC029_create_navigation_get_cache_and_method_boundaries`
- `tests/test_student_accounts.py::test_TC029_creation_requires_csrf`
- `tests/test_student_accounts.py::test_TC029_invalid_identity_fields_never_create_accounts`
- `tests/test_student_accounts.py::test_TC029_duplicate_ids_and_any_existing_login_are_rejected`
- `tests/test_student_accounts.py::test_TC029_privilege_identity_and_extra_fields_are_rejected`
- `tests/test_student_accounts.py::test_TC029_password_validation_and_no_password_redisplay`
- `tests/test_student_accounts.py::test_TC029_profile_failure_rolls_back_user_and_membership`
- `tests/test_student_accounts.py::test_TC029_database_lock_is_retryable_without_partial_account`
- `tests/test_student_accounts.py::test_TC029_duplicate_submit_and_more_than_thirty_accounts`
- `tests/test_student_accounts.py::test_TC029_optional_contact_fields_and_trimmed_id`

## TC030 — FR020, FR023

- `tests/test_student_accounts.py::test_TC030_existing_account_gets_id_login_without_losing_records`
- `tests/test_student_accounts.py::test_TC030_id_change_rejects_login_collisions_and_invalid_format`
- `tests/test_student_accounts.py::test_TC030_failed_profile_write_rolls_back_login_change`
- `tests/test_student_accounts.py::test_TC030_edit_does_not_reactivate_student`
- `tests/test_student_accounts.py::test_TC030_command_provisions_ids_and_preserves_organizer_login`
- `tests/test_student_accounts.py::test_TC030_command_rejects_mismatch_and_reserved_ids_before_password`
- `tests/test_student_accounts.py::test_TC030_fresh_demo_uses_ids_and_repeat_seeding_preserves_records`
- `tests/test_student_accounts.py::test_TC030_seed_refuses_to_replace_legacy_accounts`

## TC031 — FR024

- `tests/test_student_lifecycle.py::test_TC031_edit_page_shows_current_access_action`
- `tests/test_student_lifecycle.py::test_TC031_TC032_get_only_reviews_and_pages_are_not_cached`
- `tests/test_student_lifecycle.py::test_TC031_TC032_anonymous_and_student_requests_are_rejected`
- `tests/test_student_lifecycle.py::test_TC031_TC032_organizer_staff_and_invalid_targets_are_protected`
- `tests/test_student_lifecycle.py::test_TC031_TC032_inactive_and_mixed_role_organizers_cannot_act`
- `tests/test_student_lifecycle.py::test_TC031_TC032_csrf_and_supported_methods`
- `tests/test_student_lifecycle.py::test_TC031_TC032_confirmation_and_unexpected_fields_are_rejected`
- `tests/test_student_lifecycle.py::test_TC031_deactivation_blocks_login_and_existing_session_requests`
- `tests/test_student_lifecycle.py::test_TC031_reactivation_requires_new_login_and_old_cookies_stay_invalid`
- `tests/test_student_lifecycle.py::test_TC031_other_users_sessions_and_passwords_are_preserved`
- `tests/test_student_lifecycle.py::test_TC031_access_changes_preserve_all_account_and_event_records`
- `tests/test_student_lifecycle.py::test_TC031_waitlist_entry_keeps_position_and_remains_eligible`
- `tests/test_student_lifecycle.py::test_TC031_repeated_requests_keep_explicit_state_without_signing_out_new_login`
- `tests/test_student_lifecycle.py::test_TC031_session_failure_rolls_back_state_change`
- `tests/test_student_lifecycle.py::test_TC031_busy_failure_returns_retryable_response_without_state_change`

## TC032 — FR025

- `tests/test_student_lifecycle.py::test_TC031_TC032_get_only_reviews_and_pages_are_not_cached`
- `tests/test_student_lifecycle.py::test_TC031_TC032_anonymous_and_student_requests_are_rejected`
- `tests/test_student_lifecycle.py::test_TC031_TC032_organizer_staff_and_invalid_targets_are_protected`
- `tests/test_student_lifecycle.py::test_TC031_TC032_inactive_and_mixed_role_organizers_cannot_act`
- `tests/test_student_lifecycle.py::test_TC031_TC032_csrf_and_supported_methods`
- `tests/test_student_lifecycle.py::test_TC031_TC032_confirmation_and_unexpected_fields_are_rejected`
- `tests/test_student_lifecycle.py::test_TC032_delete_unused_account_profile_and_sessions_only`
- `tests/test_student_lifecycle.py::test_TC032_delete_inactive_unused_student`
- `tests/test_student_lifecycle.py::test_TC032_deletion_requires_exact_current_id`
- `tests/test_student_lifecycle.py::test_TC032_all_registration_statuses_block_deletion`
- `tests/test_student_lifecycle.py::test_TC032_past_attendance_and_cancelled_events_still_block_deletion`
- `tests/test_student_lifecycle.py::test_TC032_event_and_attendance_audit_references_block_deletion`
- `tests/test_student_lifecycle.py::test_TC032_new_registration_after_confirmation_get_prevents_delete`
- `tests/test_student_lifecycle.py::test_TC032_target_privilege_change_after_get_is_rechecked`
- `tests/test_student_lifecycle.py::test_TC032_protected_delete_failure_restores_profile_and_sessions`
- `tests/test_student_lifecycle.py::test_TC032_integrity_failure_does_not_partially_delete_account`
- `tests/test_student_lifecycle.py::test_TC032_busy_failure_is_retryable_and_keeps_profile`
- `tests/test_student_lifecycle.py::test_TC032_names_are_escaped_on_confirmation_pages`

