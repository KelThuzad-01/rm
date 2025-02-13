import { promises as fs } from 'fs';
import path from 'path';

async function eliminarFlowAccessesPorPatron(rutaCarpeta, patronFlow) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar solo el bloque <flowAccesses> específico que contiene el patrón en <flow>
            const regex = new RegExp(
                `<flowAccesses>\\s*<enabled>.*?</enabled>\\s*<flow>.*?${patronFlow}.*?</flow>\\s*</flowAccesses>`,
                'g'
            );

            // Eliminar solo los bloques <flowAccesses> que coincidan con el patrón en <flow>
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`Se ha eliminado correctamente el bloque(s) de flowAccesses que contienen el patrón ${patronFlow} en ${archivo}.`);
            } else {
                console.log(`No se encontró ningún bloque flowAccesses que contenga el patrón: ${patronFlow} en ${archivo}.`);
            }
        }

    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de flow
const [,, rutaCarpeta, patronFlow] = process.argv;

eliminarFlowAccessesPorPatron(rutaCarpeta, patronFlow);
