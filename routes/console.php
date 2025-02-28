<?php

use Carbon\Carbon;
use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

Artisan::command('send:errorsmdb-report', function () {
    // Obtener el día de hoy
    $today = Carbon::today();

    // Consultar los registros nuevos en errorsmdb (suponiendo que existe la columna "sent")
    $errors = DB::table('errorsmdb')
                ->whereDate('created_at', $today)
                ->where('sent', 0)
                ->get();

    if ($errors->isEmpty()) {
        $this->info('No hay nuevos registros para enviar hoy.');
        return;
    }

    // Enviar el correo o notificación con la vista de reporte
    Mail::send('emails.errors_report', ['errors' => $errors], function ($message) {
        $message->to('marlon@solucionesintegralespos.com')
                ->subject('Reporte diario de errores (errorsmdb)');
    });

    // Marcar los registros como enviados
    DB::table('errorsmdb')
      ->whereDate('created_at', $today)
      ->where('sent', 0)
      ->update(['sent' => 1]);

    $this->info('Reporte enviado exitosamente.');
})->describe('Envía un reporte diario con los nuevos registros de errorsmdb');

// Programar la tarea para que se ejecute diariamente
// Este bloque se ejecuta solo cuando la aplicación se está ejecutando en consola
if (app()->runningInConsole()) {
    $schedule = app(Schedule::class);
    $schedule->command('send:errorsmdb-report')->daily();
}
