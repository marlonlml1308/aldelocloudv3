<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Errorsmdb extends Model
{
    protected $table = 'errorsmdb';
    public function branch(): BelongsTo
    {
        return  $this->belongsTo(Branch::class, 'branchid', 'id');
    }
}
