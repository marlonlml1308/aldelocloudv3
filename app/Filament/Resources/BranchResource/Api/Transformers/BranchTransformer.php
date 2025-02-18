<?php
namespace App\Filament\Resources\BranchResource\Api\Transformers;

use Illuminate\Http\Resources\Json\JsonResource;
use App\Models\Branch;

/**
 * @property Branch $resource
 */
class BranchTransformer extends JsonResource
{

    /**
     * Transform the resource into an array.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return array
     */
    public function toArray($request)
    {
        return $this->resource->toArray();
    }
}
