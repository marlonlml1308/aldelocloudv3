<?php

namespace App\Filament\Resources\JobtitlesResource\Pages;

use App\Filament\Resources\JobtitlesResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditJobtitles extends EditRecord
{
    protected static string $resource = JobtitlesResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Actions\DeleteAction::make(),
        ];
    }
    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index'); // 🔹 Redirige al listado de productos
    }
}
