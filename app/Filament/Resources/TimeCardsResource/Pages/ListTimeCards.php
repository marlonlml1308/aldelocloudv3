<?php

namespace App\Filament\Resources\TimeCardsResource\Pages;

use App\Filament\Resources\TimeCardsResource;
use Carbon\Carbon;
use Filament\Actions;
use Filament\Resources\Components\Tab;
use Illuminate\Database\Eloquent\Builder;
use Filament\Forms\Components\TextInput;
use Filament\Resources\Pages\ListRecords;

class ListTimeCards extends ListRecords
{
    protected static string $resource = TimeCardsResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Actions\CreateAction::make(),
        ];
    }
    public function getTabs(): array
    {
        return [
            'Todos' => Tab::make(),
            'Esta Semana' => Tab::make()
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->where('workdate', '>=', Carbon::now()->startOfWeek(Carbon::MONDAY))
                ),
            'Este Mes' => Tab::make()
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->whereBetween('workdate', [
                        Carbon::now()->startOfMonth(),
                        Carbon::now()->endOfMonth()
                    ])
                ),
        ];
    }
}
