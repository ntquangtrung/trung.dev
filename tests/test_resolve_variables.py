from django.test import SimpleTestCase
from utilities.resolve_variables import VariableResolver


class ResolveVariablesTests(SimpleTestCase):

    def test_replace_existing_keys(self):
        input_str = "Hi {variable.NAME}, your ID is {variable.ID}"
        lookup = {"name": "Bob", "id": "007"}
        expected = "Hi Bob, your ID is 007"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_missing_keys_remain(self):
        input_str = "Welcome {variable.USER}, your code is {variable.CODE}"
        lookup = {"user": "Eve"}
        expected = "Welcome Eve, your code is {variable.CODE}"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_no_variable_patterns(self):
        input_str = "Just a regular string."
        lookup = {"user": "Ignored"}
        expected = "Just a regular string."
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_invalid_patterns_ignored(self):
        input_str = "Broken {variable.} and {variable.123}"
        lookup = {"": "oops", "123": "bad"}
        expected = "Broken {variable.} and {variable.123}"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_partial_overlap(self):
        input_str = "This {variable.USER} is not {variable.USER_NAME}."
        lookup = {"user": "Eve", "user_name": "EveTheGreat"}
        expected = "This Eve is not EveTheGreat."
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_nested_key_resolution(self):
        input_str = "GitHub: {variable.PROFILE.SOCIAL.GITHUB.URL}"
        lookup = {
            "profile": {"social": {"github": {"url": "https://github.com/example"}}}
        }
        expected = "GitHub: https://github.com/example"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_case_sensitive_variables_required(self):
        # Incorrect casing: should not resolve anything
        input_str = "GitHub: {variable.Profile.Social.GitHub.Url}"
        lookup = {
            "profile": {"social": {"github": {"url": "https://github.com/example"}}}
        }
        expected = "GitHub: {variable.Profile.Social.GitHub.Url}"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_dict_must_be_lowercase(self):
        # Dict keys in UPPERCASE will fail resolution
        input_str = "GitHub: {variable.PROFILE.SOCIAL.GITHUB.URL}"
        lookup = {
            "PROFILE": {"SOCIAL": {"GITHUB": {"URL": "https://github.com/example"}}}
        }
        expected = "GitHub: {variable.PROFILE.SOCIAL.GITHUB.URL}"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)

    def test_deep_nested_missing(self):
        input_str = "GitHub: {variable.PROFILE.SOCIAL.LINKEDIN.URL}"
        lookup = {
            "profile": {"social": {"github": {"url": "https://github.com/example"}}}
        }
        expected = "GitHub: {variable.PROFILE.SOCIAL.LINKEDIN.URL}"
        resolver = VariableResolver(input_str, lookup)
        self.assertEqual(resolver.resolve(), expected)
