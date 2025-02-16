<?php

namespace App\Filament\Resources\JobtitlesResource\Pages;

use App\Filament\Resources\JobtitlesResource;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateJobtitles extends CreateRecord
{
    protected static string $resource = JobtitlesResource::class;
    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index'); // 🔹 Redirige al listado de productos
    }
}
