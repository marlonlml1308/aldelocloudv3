<div class="p-4 bg-white shadow rounded">
    <h3 class="text-lg font-bold mb-2">Reporte de Errores</h3>

    <!-- Botón que llama al método enviarReporte() -->
    <button wire:click="enviarReporte" class="px-4 py-2 bg-blue-600 text-white rounded">
        Enviar Reporte de Errores
    </button>

    <!-- Mostrar la salida del comando si existe -->
    @if($result)
        <div class="mt-4 p-2 bg-gray-100 border border-gray-300">
            <strong>Resultado:</strong>
            <pre>{{ $result }}</pre>
        </div>
    @endif
</div>
