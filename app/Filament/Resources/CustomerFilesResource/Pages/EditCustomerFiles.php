<?php

namespace App\Filament\Resources\CustomerFilesResource\Pages;

use App\Filament\Resources\CustomerFilesResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditCustomerFiles extends EditRecord
{
    protected static string $resource = CustomerFilesResource::class;

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
