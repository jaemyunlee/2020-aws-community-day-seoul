from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class LimitedDynamoDBBillingMode(CloudFormationLintRule):
    """Check if resources are allowed to create"""
    id = 'E9001'
    shortdesc = 'only PAY_PER_REQUEST'
    description = 'Allows only PAY_PER_REQUEST billing mode'

    def match(self, cfn):
        matches = []
        resources = cfn.get_resources()
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get('Type', "")
            if resource_type == 'AWS::DynamoDB::Table':
                resource_properties = resource_obj.get('Properties', {})
                if not (resource_properties.get('BillingMode')
                        == 'PAY_PER_REQUEST'):
                    matches.append(
                        RuleMatch(
                            [
                                'Resources',
                                resource_name,
                                'Properties',
                                'BillingMode'
                            ],
                            'Only PAY_PER_REQUEST is allowed'
                        )
                    )

        return matches
