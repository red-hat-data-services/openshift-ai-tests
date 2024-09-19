### Using pytest_jira

pytest_jira plugin allows you to link tests to existing tickets.
To use the plugin during a test run, use '--jira'.
Issues are considered as resolved if their status appears in resolved_statuses (verified, release pending, closed).
You can mark a test to be skipped if a Jira issue is not resolved.
Example:
```
@pytest.mark.jira("XXX-1234", run=False)
```
You can mark a test to be marked as xfail if a Jira issue is not resolved.
Example:
```
@pytest.mark.jira("XXX-1234")
```

### Check the code
We use checks tools that are defined in .pre-commit-config.yaml file
To install pre-commit:
```bash
pip install pre-commit --user
pre-commit install
pre-commit install --hook-type commit-msg
```
Run pre-commit:
```bash
pre-commit run --all-files
```
pre-commit will try to fix the errors.
If some errors where fixed, git add & git commit is needed again.
commit-msg use gitlint (https://jorisroovers.com/gitlint/)

To check for PEP 8 issues locally run:
```bash
tox
```
