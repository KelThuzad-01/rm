import { promises as fs } from 'fs';
import path from 'path';

async function eliminarFieldPermissions(rutaCarpeta, objeto, campo) {
    try {
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular ajustada para coincidir con el bloque exacto
            const regex = new RegExp(
                `<fieldPermissions>\\s*<editable>.*?</editable>\\s*<field>${objeto}\\.${campo}</field>\\s*<readable>.*?</readable>\\s*</fieldPermissions>`,
                'g'
            );

            let archivoModificado = data.replace(regex, '');

            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${objeto}.${campo} OK`);
            } else {
            }
        }

    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros esperados: carpeta, objeto, campo
const [,, rutaCarpeta, objeto, campo] = process.argv;

eliminarFieldPermissions(rutaCarpeta, objeto, campo);
