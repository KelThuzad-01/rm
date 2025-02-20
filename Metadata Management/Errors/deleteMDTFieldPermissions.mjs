import { promises as fs } from 'fs';
import path from 'path';

async function eliminarFieldPermissionsPorMetadata(rutaCarpeta, nombreMetadata) {
    try {
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular para eliminar bloques de fieldPermissions que contengan el nombre del metadata
            const regex = new RegExp(
                `<fieldPermissions>\\s*<editable>.*?</editable>\\s*<field>${nombreMetadata}\\.[\\w\d_]+</field>\\s*<readable>.*?</readable>\\s*</fieldPermissions>`,
                'g'
            );

            let archivoModificado = data.replace(regex, '');

            if (archivoModificado !== data) {
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`FieldPermissions de ${nombreMetadata} eliminados correctamente.`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

const [,, rutaCarpeta, nombreMetadata] = process.argv;
eliminarFieldPermissionsPorMetadata(rutaCarpeta, nombreMetadata);
