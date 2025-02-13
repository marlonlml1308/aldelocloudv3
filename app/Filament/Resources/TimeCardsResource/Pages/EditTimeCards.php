<?php

namespace App\Filament\Resources\TimeCardsResource\Pages;

use App\Filament\Resources\TimeCardsResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditTimeCards extends EditRecord
{
    protected static string $resource = TimeCardsResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
