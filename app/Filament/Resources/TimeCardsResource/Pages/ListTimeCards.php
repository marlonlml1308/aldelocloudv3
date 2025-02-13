<?php

namespace App\Filament\Resources\TimeCardsResource\Pages;

use App\Filament\Resources\TimeCardsResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListTimeCards extends ListRecords
{
    protected static string $resource = TimeCardsResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
