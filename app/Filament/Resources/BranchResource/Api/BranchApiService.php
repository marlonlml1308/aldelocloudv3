<?php
namespace App\Filament\Resources\BranchResource\Api;

use Rupadana\ApiService\ApiService;
use App\Filament\Resources\BranchResource;
use Illuminate\Routing\Router;


class BranchApiService extends ApiService
{
    protected static string | null $resource = BranchResource::class;

    public static function handlers() : array
    {
        return [
            Handlers\CreateHandler::class,
            Handlers\UpdateHandler::class,
            Handlers\DeleteHandler::class,
            Handlers\PaginationHandler::class,
            Handlers\DetailHandler::class
        ];

    }
}
