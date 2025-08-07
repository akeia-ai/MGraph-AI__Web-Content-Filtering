from osbot_aws.apis.shell.Lambda_Shell      import lambda_shell

LAMBDA_SHELL__DEFAULT_RETURN_MESSAGE = 'This is not the lambda shell you are looking for'

@lambda_shell
def run(event, context=None):
    return LAMBDA_SHELL__DEFAULT_RETURN_MESSAGE