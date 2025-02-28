<?php

namespace App\Filament\Resources\ErrorsmdbResource\Pages;

use App\Filament\Resources\ErrorsmdbResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditErrorsmdb extends EditRecord
{
    protected static string $resource = ErrorsmdbResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
