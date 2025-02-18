<?php
namespace App\Filament\Resources\BranchResource\Api\Handlers;

use Illuminate\Http\Request;
use Rupadana\ApiService\Http\Handlers;
use App\Filament\Resources\BranchResource;
use App\Filament\Resources\BranchResource\Api\Requests\CreateBranchRequest;

class CreateHandler extends Handlers {
    public static string | null $uri = '/';
    public static string | null $resource = BranchResource::class;

    public static function getMethod()
    {
        return Handlers::POST;
    }

    public static function getModel() {
        return static::$resource::getModel();
    }

    /**
     * Create Branch
     *
     * @param CreateBranchRequest $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function handler(CreateBranchRequest $request)
    {
        $model = new (static::getModel());

        $model->fill($request->all());

        $model->save();

        return static::sendSuccessResponse($model, "Successfully Create Resource");
    }
}