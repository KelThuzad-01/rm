import { promises as fs } from 'fs';
import path from 'path';

async function eliminarCustomPermissionsPorNombre(rutaCarpeta, nombrePermiso) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular para encontrar y eliminar el bloque <customPermissions> correspondiente
            const regex = new RegExp(
                `<customPermissions>\\s*<enabled>.*?</enabled>\\s*<name>${nombrePermiso}</name>\\s*</customPermissions>`,
                'g'
            );

            let archivoModificado = data.replace(regex, '');

            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*\n/gm, '');
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${nombrePermiso} eliminado correctamente.`);
            }
        }
    } catch (err) {
        console.error('Error al eliminar permisos personalizados:', err);
    }
}

// Parámetros: ruta de la carpeta y nombre del permiso personalizado
const [,, rutaCarpeta, nombrePermiso] = process.argv;
eliminarCustomPermissionsPorNombre(rutaCarpeta, nombrePermiso);
