def pytest_report_teststatus(report, config):
    if report.skipped and "only run this test in GitHub Actions" in str(report.longrepr):
        # Hide the skip symbol, short message, and reason
        return 'skipped', '', ''