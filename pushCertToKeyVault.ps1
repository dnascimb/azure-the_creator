$fileName = "C:\TFTestCertVM1.pfx"
$fileContentBytes = get-content $fileName -Encoding Byte
$fileContentEncoded = [System.Convert]::ToBase64String($fileContentBytes)

$jsonObject=@{data="$filecontentencoded"; dataType="pfx"; password="1234" } | ConvertTo-Json

$jsonObjectBytes = [System.Text.Encoding]::UTF8.GetBytes($jsonObject)
$jsonEncoded = [System.Convert]::ToBase64String($jsonObjectBytes)

$secret = ConvertTo-SecureString -String $jsonEncoded -AsPlainText –Force
Set-AzureKeyVaultSecret -VaultName TFCertKeyVault -Name TFTestCertVM1 -SecretValue $secret