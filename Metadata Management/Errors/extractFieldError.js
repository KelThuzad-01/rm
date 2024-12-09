const { execSync } = require('child_process');
let profilePath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\profiles';
let permissionSetPath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\permissionsets';

// QA sfdx sgd:source:delta --from origin/master --output C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx
// QA sfdx sgd:source:delta --from origin/develop --output C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx

//PROD + QA
//let deployCommand = 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run';
let deployCommand = 'sf project deploy start --target-org QA-IBD --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run';

let deleteScriptTemplate = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileFieldpermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${fieldName}"';
let deleteScriptTemplateRecordType = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileRecordTypepermissionsReferences.mjs" "${profilePath}" "${recordTypeName}"';
let deleteScriptTemplateObject = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileObjectpermissionsReferences.mjs" "${profilePath}" "${objectName}"';
let deleteScriptTemplateClass = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileClasspermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${className}"';
let deleteScriptTemplateApexPage = 'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileApexPagepermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${apexPageName}"';


let fieldsFound = true;
let deploymentAttempts = 0;  // Contador de intentos de despliegue

    while (fieldsFound) {
        deploymentAttempts++;
        console.log('Starting deployment...');
        console.log(`Total deployment attempts: ${deploymentAttempts}`);

        let output;
        try {
            output = execSync(deployCommand, { encoding: 'utf-8' });
            console.log('Deployment output (success):\n', output);
        } catch (error) {
            // Capturar salida de error sin detener el script
            output = error.stdout?.toString() || error.stderr?.toString() || 'Unknown error occurred.';
            console.error('Deployment failed, processing output...');
            console.log('Command output (failure):\n', output);
        }
    
        let fieldRegex = /In field: field - no CustomField named\s+([^\s]+)\s+found/;
        let fieldMatch = output.match(fieldRegex);
        let recordTypeRegex = /In field: recordType - no RecordType named\s+([^\s]+)\s+found/;
        let recordTypeMatch = output.match(recordTypeRegex);
        let objectRegex = /In field: field - no CustomObject named\s+([^\s]+)\s+found/;
        let objectMatch = output.match(objectRegex);
        let classRegex = /In field: apexClass - no ApexClass named\s+([^\s]+)\s+found/;
        let classMatch = output.match(classRegex);
        let apexPageRegex = /In field: apexPage - no ApexPage named\s+([^\s]+)\s+found/;
        let apexPageMatch = output.match(apexPageRegex);
        //FIELDS
        if (fieldMatch && fieldMatch[1]) {
            let fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            let deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script profiles...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

            //PS
             deleteScript = deleteScriptTemplate
                .replace('${profilePath}', permissionSetPath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script permission sets...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } else if (recordTypeMatch && recordTypeMatch[1]) {
            //RECORD TYPE
            let recordTypeName = recordTypeMatch[1];
            console.log('Extracted recordType:', recordTypeName);

            let deleteScript = deleteScriptTemplateRecordType
                .replace('${profilePath}', profilePath)
                .replace('${recordTypeName}', recordTypeName);

            console.log('Running delete script profiles...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateRecordType
                .replace('${profilePath}', permissionSetPath)
                .replace('${recordTypeName}', recordTypeName);

            console.log('Running delete script permission sets...');
             deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } else if (classMatch && classMatch[1]) {
            //CLASS
            let className = classMatch[1];
            console.log('Extracted class:', className);

            let deleteScript = deleteScriptTemplateClass
                .replace('${profilePath}', profilePath)
                .replace('${className}', className);

            console.log('Running delete script profile...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateClass
                .replace('${profilePath}', permissionSetPath)
                .replace('${className}', className);

            console.log('Running delete script permission sets...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } else if (apexPageMatch && apexPageMatch[1]) {
            //APEX PAGE
            let apexPageName = apexPageMatch[1];
            console.log('Extracted apex page:', apexPageName);

            let deleteScript = deleteScriptTemplateApexPage
                .replace('${profilePath}', profilePath)
                .replace('${apexPageName}', apexPageName);

            console.log('Running delete script profiles...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateApexPage
                .replace('${profilePath}', permissionSetPath)
                .replace('${apexPageName}', apexPageName);

            console.log('Running delete script permission sets...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
        } 
        else if (objectMatch && objectMatch[1]) {
            let objectName = objectMatch[1];
            console.log('Extracted objectName:', objectName);

            let deleteScript = deleteScriptTemplateObject
                .replace('${profilePath}', profilePath)
                .replace('${objectName}', objectName);

            console.log('Running delete script profiles...');
            let deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);

            let fieldName = fieldMatch[1];
            console.log('Extracted field:', fieldName);

            deleteScript = deleteScriptTemplate
                .replace('${profilePath}', profilePath)
                .replace('${fieldName}', fieldName);

            console.log('Running delete script profile...');
            deleteOutput = execSync(deleteScript, { encoding: 'utf-8' });
            console.log('Delete script output:\n', deleteOutput);
            //PS
             deleteScript = deleteScriptTemplateObject
                .replace('${profilePath}', permissionSetPath)
                .replace('${objectName}', objectName);

            console.log('Running delete script profiles...');
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
            console.log('\u0007'); // Reproduce un sonido de campana
            fieldsFound = false;
        }
    }