<?php

namespace App\Filament\Resources\ErrorsmdbResource\Pages;

use App\Filament\Resources\ErrorsmdbResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListErrorsmdbs extends ListRecords
{
    protected static string $resource = ErrorsmdbResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Actions\CreateAction::make(),
        ];
    }
}
