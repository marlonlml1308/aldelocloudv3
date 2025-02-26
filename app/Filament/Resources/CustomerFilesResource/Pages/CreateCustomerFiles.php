<?php

namespace App\Filament\Resources\CustomerFilesResource\Pages;

use App\Filament\Resources\CustomerFilesResource;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateCustomerFiles extends CreateRecord
{
    protected static string $resource = CustomerFilesResource::class;
}
