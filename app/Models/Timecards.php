<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Timecards extends Model
{
    use HasFactory;
    public function branch(): BelongsTo
    {
        return  $this->belongsTo(Branch::class, 'branchid', 'id');
    }

    public function employees(): BelongsTo
    {
        return  $this->belongsTo(Employees::class, 'employeeid');
    }
}
