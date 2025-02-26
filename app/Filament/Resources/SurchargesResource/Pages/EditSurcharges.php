<?php

namespace App\Filament\Resources\SurchargesResource\Pages;

use App\Filament\Resources\SurchargesResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditSurcharges extends EditRecord
{
    protected static string $resource = SurchargesResource::class;

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
