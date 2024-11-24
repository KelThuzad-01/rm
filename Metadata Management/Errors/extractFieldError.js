let { execSync } = require('child_process');

//paso previo, desde la rama correspondiente: sfdx sgd:source:delta --from origin/ramaDestino --output .
let profilePath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\profiles';
let permissionSetPath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\permissionsets';
//prod: 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run'
//qa: 'sf project deploy start --target-org QA-IBD --manifest manifest\\package\\package.xml --ignore-conflicts --ignore-warnings -l NoTestRun --dry-run'
let deployCommand = 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run';


let deleteScriptTemplate = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileFieldpermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${fieldName}"';
let deleteScriptTemplateRecordType = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileRecordTypepermissionsReferences.mjs" "${profilePath}" "${recordTypeName}"';
let deleteScriptTemplateObject = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileObjectpermissionsReferences.mjs" "${profilePath}" "${objectName}"';

let fieldsFound = true;
try {
    while (fieldsFound) {
        console.log('Starting deployment...');

        let output;
        try {
            output = execSync(deployCommand, { encoding: 'utf-8' });
        } catch (error) {
            output = error.stdout || '';
            console.error('Deployment failed, processing output...');
        }
        console.log('Command output:\n', output);
        let fieldRegex = /In field: field - no CustomField named\s+([^\s]+)\s+found/;
        let fieldMatch = output.match(fieldRegex);
        let recordTypeRegex = /In field: recordType - no RecordType named\s+([^\s]+)\s+found/;
        let recordTypeMatch = output.match(recordTypeRegex);
        let objectRegex = /In field: field - no CustomObject named\s+([^\s]+)\s+found/;
        let objectMatch = output.match(objectRegex);
        if (fieldMatch && fieldMatch[1]) {
            let fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            let deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

            //PS
             deleteScript = deleteScriptTemplate
                .replace('${profilePath}', permissionSetPath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } else if (recordTypeMatch && recordTypeMatch[1]) {
            let recordTypeName = recordTypeMatch[1];
            console.log('Extracted recordType:', recordTypeName);

            let deleteScript = deleteScriptTemplateRecordType
                .replace('${profilePath}', profilePath)
                .replace('${recordTypeName}', recordTypeName);

            console.log('Running delete script...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateRecordType
                .replace('${profilePath}', permissionSetPath)
                .replace('${recordTypeName}', recordTypeName);

            console.log('Running delete script...');
             deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        }else if (objectMatch && objectMatch[1]) {
            let objectName = objectMatch[1];
            console.log('Extracted objectName:', objectName);

            let deleteScript = deleteScriptTemplateObject
                .replace('${profilePath}', profilePath)
                .replace('${objectName}', objectName);

            console.log('Running delete script...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

            let fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateObject
                .replace('${profilePath}', permissionSetPath)
                .replace('${objectName}', objectName);

            console.log('Running delete script...');
             deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

             fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            deleteScript = deleteScriptTemplate
                .replace('${profilePath}', permissionSetPath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

        }else {
            console.log('No further action required.');
            fieldsFound = false;
        }
    }
} catch (error) {
    console.error('Unexpected error during script execution:', error.message);
    process.exit(1);
}