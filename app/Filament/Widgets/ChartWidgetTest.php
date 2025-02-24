<?php

namespace App\Filament\Widgets;

use App\Models\Groups;
use App\Models\Products;
use Filament\Widgets\ChartWidget;
use Flowframe\Trend\Trend;
use Flowframe\Trend\TrendValue;

class ChartWidgetTest extends ChartWidget
{
    protected static ?string $heading = 'Ventas Por Medio de Pago';

    protected function getData(): array
    {
        // Obtener la cantidad de productos agrupados por categoría, filtrando condiciones
        $data = Products::selectRaw('menugroupid, COUNT(*) as total')
            ->where('menuiteminactive', false) // Productos activos
            ->where('menuitemtype', 1) // Solo productos de tipo 1
            ->whereHas('groups', function ($query) {
                $query->where('menugroupinactive', false); // Solo categorías activas
            })
            ->groupBy('menugroupid')
            ->with('groups') // Para obtener los nombres de las categorías
            ->get();
        $colors =  ['Red', 'Orange', 'Yellow', 'Green', 'Blue'];
        return [
            'datasets' => [
                [
                    'label' => 'Blog posts created',
                    'data' => $data->pluck('total'),
                    'backgroundColor' => array_slice($colors, 0, $data->count()),
                ],
            ],
            'labels' => $data->map(fn ($item) => $item->groups->menugrouptext ?? 'Sin Grupo'),
        ];
    }

    protected function getType(): string
    {
        return 'pie';
    }
}
