import { promises as fs } from 'fs';
import path from 'path';

// Elimina los customMetadataTypeAccesses en PermissionSet/Perfiles a partir de un objeto

// Ejemplo de ejecución manual:
// node deleteCustomMetadataAccesses.mjs "C:\Users\aberdun\Downloads\iberdrola-sfdx\force-app\main\default\profiles" "IBD_IBERGO_Control_de_Estados__mdt"

async function eliminarCustomMetadataAccesses(rutaCarpeta, patronMetadata) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar y eliminar el bloque <customMetadataTypeAccesses>
            const regex = new RegExp(
                `<customMetadataTypeAccesses>\\s*<enabled>.*?</enabled>\\s*<name>${patronMetadata.replace(/[-/\\]/g, '\\\\$&')}</name>\\s*</customMetadataTypeAccesses>`,
                'gs'
            );

            // Eliminar los bloques que coincidan con el patrón en <name>
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${patronMetadata} OK`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de metadata
const [,, rutaCarpeta, patronMetadata] = process.argv;

eliminarCustomMetadataAccesses(rutaCarpeta, patronMetadata);