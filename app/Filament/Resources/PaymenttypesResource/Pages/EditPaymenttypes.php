<?php

namespace App\Filament\Resources\PaymenttypesResource\Pages;

use App\Filament\Resources\PaymenttypesResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditPaymenttypes extends EditRecord
{
    protected static string $resource = PaymenttypesResource::class;

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
