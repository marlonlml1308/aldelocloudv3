<?php

namespace App\Filament\Resources\ModulesResource\Pages;

use App\Filament\Resources\ModulesResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditModules extends EditRecord
{
    protected static string $resource = ModulesResource::class;

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
