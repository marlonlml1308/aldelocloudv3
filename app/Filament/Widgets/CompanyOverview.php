<?php

namespace App\Filament\Widgets;

use App\Models\Branch;
use App\Models\Categories;
use App\Models\Employees;
use App\Models\Groups;
use App\Models\Products;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;
use Filament\Support\Enums\IconPosition;

class CompanyOverview extends BaseWidget
{
    protected function getStats(): array
    {
        return [
            Stat::make('Sucursales', Branch::query()->count())
            ->descriptionIcon('heroicon-o-building-storefront', IconPosition::Before),
            Stat::make('Categorias', Categories::query()->count()),
            Stat::make('Grupos', Groups::query()->count()),
            Stat::make('Productos', Products::query()->count()),
            Stat::make('Empleados', Employees::query()->count()),
        ];
    }
}
