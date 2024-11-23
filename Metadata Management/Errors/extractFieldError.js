const { execSync } = require('child_process');

//paso previo, desde la rama correspondiente: sfdx sgd:source:delta --from origin/ramaDestino --output .
const profilePath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\profiles';
//prod: 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run'
//qa: 'sf project deploy start --target-org QA-IBD --manifest manifest\\package\\package.xml --ignore-conflicts --ignore-warnings -l NoTestRun --dry-run'
const deployCommand = 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run';
const deleteScriptTemplate = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileFieldpermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${fieldName}"';
const deleteScriptTemplateRecordType = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileRecordTypepermissionsReferences.mjs" "${profilePath}" "${recordTypeName}"';
const deleteScriptTemplateObject = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileObjectpermissionsReferences.mjs" "${profilePath}" "${objectName}"';


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

        // Buscar el texto entre "named" y "found"
        const fieldRegex = /In field: field - no CustomField named\s+([^\s]+)\s+found/;
        const fieldMatch = output.match(fieldRegex);

        const recordTypeRegex = /In field: recordType - no RecordType named\s+([^\s]+)\s+found/;
        const recordTypeMatch = output.match(recordTypeRegex);

        const objectRegex = /In field: field - no CustomObject named\s+([^\s]+)\s+found/;
        const objectMatch = output.match(objectRegex);

        if (fieldMatch && fieldMatch[1]) {
            const fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            // Lanzar el script de eliminación con el campo como parámetro
            const deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            const deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } else if (recordTypeMatch && recordTypeMatch[1]) {
            const recordTypeName = recordTypeMatch[1];
            console.log('Extracted recordType:', recordTypeName);

            // Lanzar el script de eliminación con el campo como parámetro
            const deleteScript = deleteScriptTemplateRecordType
                .replace('${profilePath}', profilePath)
                .replace('${recordTypeName}', recordTypeName);

            console.log('Running delete script...');
            const deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        }else if (objectMatch && objectMatch[1]) {
            const objectName = objectMatch[1];
            console.log('Extracted objectName:', objectName);

            // Lanzar el script de eliminación con el campo como parámetro
            const deleteScript = deleteScriptTemplateObject
                .replace('${profilePath}', profilePath)
                .replace('${objectName}', objectName);

            console.log('Running delete script...');
            const deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

            const fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            // Lanzar el script de eliminación con el campo como parámetro
            deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        }else {
            console.log('No further action required.');
            fieldsFound = false; // Salir del bucle
        }
    }
} catch (error) {
    console.error('Unexpected error during script execution:', error.message);
    process.exit(1);
}
