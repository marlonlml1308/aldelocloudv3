<?php

namespace App\Filament\Resources\SurchargesResource\Pages;

use App\Filament\Resources\SurchargesResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListSurcharges extends ListRecords
{
    protected static string $resource = SurchargesResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
