# CloudFormation SAML Identity Provider CustomResource and Roles
This is a Cloudformation Custom Resource Lambda and template that can be used to provision SAML Identity Providers in an AWS Account. The Custom Resource can create an Identity Provider using SAML Metadata provided in a string, via the `Metadata` property, or it can retrieve the Metadata via a Url using the `MetadataUrl` property.

The CloudFormation template [`saml-idp-cfn-with-roles.yml`](saml-idp-cfn-with-roles.yml) does the following:
1. Creates a Lambda Execution Role with permission to create, update, and delete SAML Identity Providers and write to CloudWatch Logs
2. Creates a Lambda function that is used by CloudFormation Custom Resource, `Custom::SAMLIdentityProvider`. The source code is in [src/index.py](src/index.py). 
3. Uses `Custom::SAMLIdentityProvider` to create a SAML Identity Provider in the AWS Account
4. Creates several standard roles (and attached policies) in the account:
    - AWS-AccountAdmin (AdministratorAccess)
    - AWS-PowerUser (PowerUserAccess)
    - AWS-NetworkAdmin (NetworkAdministrator)
    - AWS-SysAdmin (SystemAdministrator)
    - AWS-Developer (DataScientist)
    - AWS-ReadOnly (ReadOnlyAccess)
    - AWS-Billing (Billing)
    - AWS-ReadOnlyBilling (ReadOnlyBillingPolicy)

    Each of the roles has a trust policy that allows the SAML Identity Provider to federate.


## Deployment instructions

1. (Optional) Customize the `saml-idp-cfn-with-roles.yml` template. 
2. Log in and go to the CloudFormation console and create a new stack.
3. Upload the `saml-idp-cfn-with-roles.yml` template
4. Enter the parameters:
    1. Name: The name that will be given the the SAML Identity Provider (if using the [Shibboleth Configuration Guide]https://github.com/senorkrabs/aws-shibboleth-config-guide/), set this to `shibboleth`)
    2. Metadata: Optional. The IdP Metadata that will be used. It is recommended that you leave this blank and use MetadataUrl to dynamically retrieve the IdP Metadata instead.
    3. MetadataUrl: The URL where the IdP Metadata can be downloaded. For Shibboleth, this is usually at `https://shibboleth-host/idp/shibboleth` by default.

5. Finish creating the stack and wait for it to complete.
6. Once complete, confirm 

**Pro tip**: You can use this template in a [StackSet](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html) to [deploy to multiple accounts automatically](https://aws.amazon.com/blogs/aws/new-use-aws-cloudformation-stacksets-for-multiple-accounts-in-an-aws-organization/). 

## Shibboleth
You can use this template to configure any SAML Identity Provider. However, if you're using Shibboleth there is an additional guide that walks through the Shibboleth IdP configuration that you can follow after deploying the SAML Identity Provider and roles using `saml-idp-cfn-with-roles.yaml`:

### [Shibboleth Configuration Guide](https://github.com/senorkrabs/aws-shibboleth-config-guide/)

## Custom::SAMLIdentityProvider Usage Details

To use the custom resource in CloudFormation, make sure the Lambda and Lambda Execution Role are defined in the Cloudformation Template, then declare under `Resources: `

### Create a SAML Identity Provider with Metadata from a Url
```yaml
  SAMLProvider:
    Type: Custom::SAMLIdentityProvider
    Properties:
      # The Arn of the Lambda function that will handle this CustomResource request. This is declared earlier in the template.
      ServiceToken: !GetAtt LambdaSAMLIdentityProviderCustomResource.Arn
      # The name of the SAML Identity Provider to create. Must be unique.
      Name: !Ref Name
      # The SAML IDP Metadata that will be used for the creation of the SAML Identity Provider. Leave this blank if the metadata will be retrieved by Url
      Metadata: ''
      # There Url where the SAML IDP Metadata can be downloaded. This is only applied if the Metadata parameter is empty.
      MetadataUrl: http://my-idp.example.com/idp/metadata.xml
```
### Create a SAML Identity Provider with Metadata embedded.
```yaml
  SAMLProvider:
    Type: Custom::SAMLIdentityProvider
    Properties:
      # The Arn of the Lambda function that will handle this CustomResource request. This is declared earlier in the template.
      ServiceToken: !GetAtt LambdaSAMLIdentityProviderCustomResource.Arn
      # The name of the SAML Identity Provider to create. Must be unique.
      Name: !Ref Name
      # The SAML IDP Metadata that will be used for the creation of the SAML Identity Provider. Leave this blank if the metadata will be retrieved by Url
      Metadata: |
        <EntityDescriptor entityID="https://myidp.example.com/idp/shibboleth" xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:shibmd="urn:mace:shibboleth:metadata:1.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
              <Extensions>
                <shibmd:Scope regexp="false">example.com</shibmd:Scope>
              </Extensions>
              <KeyDescriptor use="signing">
                <ds:KeyInfo>
                  <ds:X509Data>
                    <ds:X509Certificate>
          MIIDTDCCAjSgAwIBAgIJAN0eZsCFJj2SMA0GCSqGSIb3DQEBCwUAMCYxJDAiBgNV
          BAMMG3NoaWJib2xldGgubGFzdG5hbWVib3lkLmNvbTAeFw0yMDAzMDkwMDE1MzNa
          Fw0yNTAzMDgwMDE1MzNaMCYxJDAiBgNVBAMMG3NoaWJib2xldGgubGFzdG5hbWVi
          b3lkLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALcxXBiT2tf2
          OaoqltRNQHWbKLAPW1aMIEXAn4FOE5gCC2S98NgBQ3kFYLFJ/V9MV9g9yg4+uvch
          3/YlIBfjksrezAwaDOwUhbY+NOoeSiKKhvyHyNVrA4//ZbwfVT4nMGUJV3V/zDE9
          8HVq3RkfyIT5fVfz0xNwaF...
                    </ds:X509Certificate>
                  </ds:X509Data>
                </ds:KeyInfo>
              </KeyDescriptor>
              <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://myidp.example.com/idp/profile/SAML2/Redirect/SSO"/>
              <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://myidp.example.com/idp/profile/SAML2/POST/SSO"/>
              <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST-SimpleSign" Location="https://myidp.example.com/idp/profile/SAML2/POST-SimpleSign/SSO"/>
              <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:SOAP" Location="https://myidp.example.com/idp/profile/SAML2/SOAP/ECP"/>
            </IDPSSODescriptor>
          </EntityDescriptor>


      # There Url where the SAML IDP Metadata can be downloaded. This is only applied if the Metadata parameter is empty.
      MetadataUrl: ''
```