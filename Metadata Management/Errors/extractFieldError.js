const { execSync } = require('child_process');

const profilePath = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\profiles';

const deployCommand = 'sf project deploy start --target-org QA-IBD --manifest manifest\\package\\package.xml --ignore-conflicts --ignore-warnings -l NoTestRun --dry-run';
const deleteScriptTemplate = 'node "C:\\Users\\aberdun\\OneDrive - SEIDOR SOLUTIONS S.L\\Escritorio\\deletePermissionSetProfileFieldpermissionsReferencesByObjectOrField.mjs" "${profilePath}" "${fieldName}"';

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
        const fieldRegex = /named\s+([^\s]+)\s+found/;
        const fieldMatch = output.match(fieldRegex);

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

            console.log('Retrying deployment to check for more issues...');
        } else {
            console.log('No field found in deployment output. No further action required.');
            fieldsFound = false; // Salir del bucle
        }
    }
} catch (error) {
    console.error('Unexpected error during script execution:', error.message);
    process.exit(1);
}
