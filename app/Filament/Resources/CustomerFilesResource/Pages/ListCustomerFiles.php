<?php

namespace App\Filament\Resources\CustomerFilesResource\Pages;

use App\Filament\Resources\CustomerFilesResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListCustomerFiles extends ListRecords
{
    protected static string $resource = CustomerFilesResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Actions\CreateAction::make(),
        ];
    }
}
