import { promises as fs } from 'fs';
import path from 'path';

// Elimina las referencias a UserPermissions en perfiles y conjuntos de permisos

async function eliminarUserPermissionsPorPatron(rutaCarpeta, patronPermission) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar y eliminar el bloque <userPermissions> específico
            const regex = new RegExp(
                `<userPermissions>\s*<enabled>.*?</enabled>\s*<name>${patronPermission}</name>\s*</userPermissions>`,
                'g'
            );

            // Eliminar los bloques que coincidan con el patrón
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                archivoModificado = archivoModificado.replace(/^\s*[]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`Se ha eliminado correctamente el bloque(s) de userPermissions que contienen el patrón ${patronPermission} en ${archivo}.`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de userPermission
const [,, rutaCarpeta, patronPermission] = process.argv;

eliminarUserPermissionsPorPatron(rutaCarpeta, patronPermission);
