import { promises as fs } from 'fs';
import path from 'path';

// Elimina las referencias a LayoutAssignments en perfiles y conjuntos de permisos

async function eliminarLayoutAssignmentsPorPatron(rutaCarpeta, patronLayout) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar y eliminar el bloque <layoutAssignments>
            const regex = new RegExp(`<layoutAssignments>[\\s\\S]*?<layout>\\s*${patronLayout}\\s*</layout>[\\s\\S]*?</layoutAssignments>`, 'g');


            // Eliminar los bloques que coincidan con el patrón
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`Se ha eliminado correctamente el bloque(s) de layoutAssignments que contienen el patrón ${patronLayout} en ${archivo}.`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de layout
const [,, rutaCarpeta, patronLayout] = process.argv;

eliminarLayoutAssignmentsPorPatron(rutaCarpeta, patronLayout);
