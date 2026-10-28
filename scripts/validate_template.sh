#!/usr/bin/env bash
set -e

echo "========================================================"
echo "EWB VPC Peering Project - Local Template & Syntax Validation"
echo "========================================================"

TEMPLATE_FILE="infrastructure/vpc-peering.yaml"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: CloudFormation template $TEMPLATE_FILE not found!"
    exit 1
fi

echo "[1/3] Checking CloudFormation YAML syntax with cfn-lint / python..."
python3 -c "
import yaml

class CfnLoader(yaml.SafeLoader):
    pass

def cfn_tag_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return {tag_suffix: loader.construct_scalar(node)}
    elif isinstance(node, yaml.SequenceNode):
        return {tag_suffix: loader.construct_sequence(node)}
    elif isinstance(node, yaml.MappingNode):
        return {tag_suffix: loader.construct_mapping(node)}

CfnLoader.add_multi_constructor('!', cfn_tag_constructor)

with open('$TEMPLATE_FILE', 'r') as f:
    yaml.load(f, Loader=CfnLoader)
print('==> CloudFormation YAML syntax is valid.')
"

echo "[2/3] Linting CloudFormation template with cfn-lint..."
cfn-lint "$TEMPLATE_FILE"
echo "==> cfn-lint passed with zero errors/warnings."

echo "[3/3] Checking required resource definitions in template..."
python3 -c "
import yaml

class CfnLoader(yaml.SafeLoader):
    pass

def cfn_tag_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return {tag_suffix: loader.construct_scalar(node)}
    elif isinstance(node, yaml.SequenceNode):
        return {tag_suffix: loader.construct_sequence(node)}
    elif isinstance(node, yaml.MappingNode):
        return {tag_suffix: loader.construct_mapping(node)}

CfnLoader.add_multi_constructor('!', cfn_tag_constructor)

with open('$TEMPLATE_FILE', 'r') as f:
    cfn = yaml.load(f, Loader=CfnLoader)

resources = cfn.get('Resources', {})

required_resources = [
    'VpcA', 'PublicSubnetA', 'PrivateSubnetA', 'InternetGatewayA', 'VpcGatewayAttachmentA',
    'PublicRouteTableA', 'PrivateRouteTableA',
    'VpcB', 'PrivateSubnetB', 'PrivateRouteTableB',
    'VPCPeeringConnection', 'PublicRoutePeeringA', 'PrivateRoutePeeringA', 'PrivateRoutePeeringB',
    'BastionSecurityGroup', 'AppASecurityGroup', 'AppBSecurityGroup',
    'BastionInstance', 'AppAInstance', 'AppBInstance'
]

missing = [r for r in required_resources if r not in resources]

if missing:
    print('[-] Missing required CloudFormation resources:', missing)
    exit(1)

print('[+] All 20 required AWS infrastructure resources are present.')
"

echo "========================================================"
echo "SUCCESS: CloudFormation template validation completed!"
echo "========================================================"
