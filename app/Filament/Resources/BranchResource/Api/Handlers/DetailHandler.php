<?php

namespace App\Filament\Resources\BranchResource\Api\Handlers;

use App\Filament\Resources\SettingResource;
use App\Filament\Resources\BranchResource;
use Rupadana\ApiService\Http\Handlers;
use Spatie\QueryBuilder\QueryBuilder;
use Illuminate\Http\Request;
use App\Filament\Resources\BranchResource\Api\Transformers\BranchTransformer;

class DetailHandler extends Handlers
{
    public static string | null $uri = '/{id}';
    public static string | null $resource = BranchResource::class;


    /**
     * Show Branch
     *
     * @param Request $request
     * @return BranchTransformer
     */
    public function handler(Request $request)
    {
        $id = $request->route('id');
        
        $query = static::getEloquentQuery();

        $query = QueryBuilder::for(
            $query->where(static::getKeyName(), $id)
        )
            ->first();

        if (!$query) return static::sendNotFoundResponse();

        return new BranchTransformer($query);
    }
}
