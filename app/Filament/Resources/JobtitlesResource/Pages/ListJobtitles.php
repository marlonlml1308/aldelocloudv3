<?php

namespace App\Filament\Resources\JobtitlesResource\Pages;

use App\Filament\Resources\JobtitlesResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListJobtitles extends ListRecords
{
    protected static string $resource = JobtitlesResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
