<?php

namespace App\Filament\Resources\PaymenttypesResource\Pages;

use App\Filament\Resources\PaymenttypesResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListPaymenttypes extends ListRecords
{
    protected static string $resource = PaymenttypesResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
