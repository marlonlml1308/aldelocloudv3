<?php

namespace App\Filament\Resources\DiscountsResource\Pages;

use App\Filament\Resources\DiscountsResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditDiscounts extends EditRecord
{
    protected static string $resource = DiscountsResource::class;

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
