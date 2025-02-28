<?php

namespace App\Filament\Widgets;

use Filament\Widgets\Widget;
use Illuminate\Support\Facades\Artisan;

class ErrorsReportWidget extends Widget
{
    // Título del widget
    protected static ?string $heading = 'Reporte de Errores';

    // Nombre de la vista asociada al widget
    protected static string $view = 'errors-report-widget';

    // Variable para almacenar la salida del comando
    public string $result = '';

    // Método que se invoca cuando se hace clic en el botón
    public function enviarReporte()
    {
        // Llama al comando definido en routes/console.php
        Artisan::call('send:errorsmdb-report');

        // Captura la salida del comando
        $this->result = Artisan::output();
    }
}
