import { promises as fs } from 'fs';
import path from 'path';

function contarPermisos(bloque) {
    const editable = /<editable>\s*true\s*<\/editable>/i.test(bloque) ? 1 : 0;
    const readable = /<readable>\s*true\s*<\/readable>/i.test(bloque) ? 1 : 0;
    return editable + readable;
}

async function eliminarDuplicadosConMenosPermisos(rutaCarpeta) {
    try {
        const archivos = await fs.readdir(rutaCarpeta);

        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);
            const dataOriginal = await fs.readFile(rutaArchivo, 'utf8');

            const matches = dataOriginal.match(/<fieldPermissions>[\s\S]*?<\/fieldPermissions>/g);
            if (!matches) continue;

            const fieldMap = new Map();

            for (const bloque of matches) {
                const fieldMatch = bloque.match(/<field>(.*?)<\/field>/);
                if (fieldMatch) {
                    const fieldValue = fieldMatch[1].trim();
                    const lista = fieldMap.get(fieldValue) || [];
                    lista.push(bloque.trim());
                    fieldMap.set(fieldValue, lista);
                }
            }

            let dataModificado = dataOriginal;

            for (const [fieldName, bloques] of fieldMap.entries()) {
                if (bloques.length > 1) {
                    // Eliminar duplicados exactos, conservar uno
                    const bloquesUnicos = [...new Set(bloques)];

                    // Si todos los bloques son iguales, conservar uno solo
                    if (bloquesUnicos.length === 1) {
                        const bloqueAConservar = bloquesUnicos[0];
                        const cantidadADuplicar = bloques.length - 1;
                        if (cantidadADuplicar > 0) {
                            console.warn(`✂️  Eliminando ${cantidadADuplicar} duplicado(s) exacto(s) en "${archivo}" para el campo "${fieldName}"`);
                            let eliminados = 0;
                            for (let i = 0; i < cantidadADuplicar; i++) {
                                dataModificado = dataModificado.replace(bloqueAConservar, '');
                                eliminados++;
                            }
                        }
                    } else {
                        // Caso con bloques distintos: conservar el de más permisos
                        const bloquesOrdenados = bloquesUnicos.sort((a, b) => contarPermisos(b) - contarPermisos(a));
                        const bloqueAConservar = bloquesOrdenados[0];
                        const bloquesAEliminar = bloques.filter(b => b !== bloqueAConservar);

                        console.warn(`✂️  Eliminando duplicados con menos permisos en "${archivo}" para el campo "${fieldName}"`);

                        for (const bloque of bloquesAEliminar) {
                            // Solo eliminar una instancia exacta, no todas
                            dataModificado = dataModificado.replace(bloque, '');
                        }
                    }

                    // Limpiar líneas vacías
                    dataModificado = dataModificado.replace(/^\s*[\r\n]/gm, '');
                }
            }

            if (dataModificado !== dataOriginal) {
                await fs.writeFile(rutaArchivo, dataModificado, 'utf8');
                console.log(`✅ Archivo actualizado: ${archivo}`);
            }
        }

    } catch (err) {
        console.error('❌ Error:', err);
    }
}

const [,, rutaCarpeta] = process.argv;

if (!rutaCarpeta) {
    console.error('❌ Debes especificar la ruta a la carpeta.');
    process.exit(1);
}

eliminarDuplicadosConMenosPermisos(rutaCarpeta);
