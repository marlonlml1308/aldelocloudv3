<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
class Products extends Model
{
    Use HasFactory;
    public function categories(): BelongsTo
    {
        return  $this->belongsTo(Categories::class);
    }
    public function groups(): BelongsTo
    {
        return  $this->belongsTo(Groups::class);
    }
}
