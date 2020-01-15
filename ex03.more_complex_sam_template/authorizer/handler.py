def lambda_handler(event, context):
    token = event.get("authorizationToken")

    if token == 'catlover':
        return generate_policy('Georges St-Pierre', 'Allow')
    else:
        return generate_policy(None, 'Deny')


def generate_policy(principal_id, effect):
    if effect:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": "*"
                }
            ]
        }
        response_data = {
            "principalId": principal_id,
            "policyDocument": policy_document
        }
        return response_data
