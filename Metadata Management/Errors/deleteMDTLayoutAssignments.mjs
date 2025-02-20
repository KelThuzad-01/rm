import { promises as fs } from 'fs';
import path from 'path';

async function eliminarLayoutAssignmentsPorMetadata(rutaCarpeta, nombreMetadata) {
    try {
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular para eliminar bloques de layoutAssignments que comiencen con el nombre del metadata
            const regex = new RegExp(
                `<layoutAssignments>\\s*<layout>${nombreMetadata}-[\\w\\s\\d_]+</layout>\\s*</layoutAssignments>`,
                'g'
            );

            let archivoModificado = data.replace(regex, '');

            if (archivoModificado !== data) {
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`LayoutAssignments de ${nombreMetadata} eliminados correctamente.`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

const [,, rutaCarpeta, nombreMetadata] = process.argv;
eliminarLayoutAssignmentsPorMetadata(rutaCarpeta, nombreMetadata);
